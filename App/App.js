/**
 * Sample React Native App
 * https://github.com/facebook/react-native
 *
 * @format
 * @flow strict-local
 */
import 'react-native-gesture-handler';
import React, { useState, useRef, useEffect } from 'react';
import {
  SafeAreaView,
  StyleSheet,
  ScrollView,
  View,
  Text,
  StatusBar,
  Dimensions, 
  Alert, 
  ActivityIndicator,
  Button, 
  TouchableHighlight,
  Image,
  TextInput
} from 'react-native';

import { NavigationContainer } from '@react-navigation/native';
import { createStackNavigator } from '@react-navigation/stack';

import Geolocation from '@react-native-community/geolocation';

import { RNCamera } from 'react-native-camera';

const CaptureButton: ({buttonDisabled: bool, onClick: () => mixed}) => React$Node = (props) => {
  return (
    <TouchableHighlight 
      style={{
        marginBottom:30,
        width:160,
        borderRadius:10,
        backgroundColor: "white",
        alignSelf: "center"
      }} 
      disabled={props.buttonDisabled}>
      <Button onPress={props.onClick} disabled={props.buttonDisabled} title="Capture" accessibilityLabel="Learn more about this button"/>
    </TouchableHighlight>
  );
};

const DetailsScreen: ({ route : any, navigation: any }) => React$Node = ({ route, navigation }) => {
  const [address, setAddress] = React.useState('');

  useEffect(() => {
    const fetchAddress = async () => { 
      const geo = await new Promise((resolve, reject) => Geolocation.getCurrentPosition(info => resolve(info), err => reject(err), { enableHighAccuracy: true}));
      const response = await fetch(`https://mobile.um.warszawa.pl/cxf/bgik/rest/nearestPoint?latitude=${geo.coords.latitude}&longitude=${geo.coords.longitude}`);
      const addr = await response.json();
      setAddress(`${addr.address} ${addr.postalCode}`);
    };

    fetchAddress();
  }, []);  

  return (
    <View 
      style={{
        flex: 1,
        backgroundColor: '#fff',
        alignItems: 'stretch',
        justifyContent: 'flex-start',	
      }}> 
      <ScrollView style={{
            flex: 1,
          }}>
        <Image
          style={{
            height: Dimensions.get('window').height,
            width: Dimensions.get('window').width,
          }}
          source={{ uri: route.params.data.uri }}
        />
      </ScrollView>
      <View
        style={{
          flex: 2
        }}>
        <View
          style={{
            flexDirection: 'row',
            height: 30,
            margin: 10
          }}>
          <View
            style={{
              justifyContent: 'center',
              alignItems: 'center'
            }}>
            <Text style={{ marginRight: 10}}>Adres:</Text>
          </View>
          <TextInput
            style={{ borderColor: 'gray', padding: 3, borderWidth: 1, flex: 1}}
            onChangeText={text => setAddress(text)}
            value={address}
          />
        </View>
      </View>
    </View>
  );
};

const CameraScreen: ({ navigation: any }) => React$Node = ({ navigation }) => {
  const [isLoading, setIsLoading] = useState(false);
  const [identifiedAs, setIdentifiedAs] = useState("");

  const camera = useRef(null);

  const takePicture = async function() {
    let cam = camera.current;
		if (cam) {
      cam.pausePreview();
      setIsLoading(true);
			const data = await cam.takePictureAsync({ base64: false });
      setIdentifiedAs("identifiedImage");
      setIsLoading(false);

      if (camera.current) {
        camera.current.resumePreview();
      }
      navigation.navigate('Details', { data: data })
		}
	}

  return (
    <View style={{
            flex: 1,
            backgroundColor: '#fff',
          }}>
      <RNCamera ref={camera} 
                style={{
                  flex: 1,
                }} 
                captureAudio={false}>
        <ActivityIndicator 
          size="large" 
          style={{
            flex: 1,
            alignItems: 'center',
            justifyContent: 'center',
          }} 
          color="#fff" 
          animating={isLoading}/>
        <CaptureButton buttonDisabled={isLoading} onClick={takePicture}/>
      </RNCamera>
    </View>
  );
};

const Stack = createStackNavigator();

const App: () => React$Node = () => {
  return (
    <NavigationContainer>
      <Stack.Navigator>
        <Stack.Screen name="Home" component={CameraScreen} />
        <Stack.Screen name="Details" component={DetailsScreen} />
      </Stack.Navigator>
    </NavigationContainer>
  );
};

export default App;